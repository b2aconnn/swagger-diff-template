# Swagger 변경 감지 알람 시스템 설계

## 배경 및 목적

API spec이 변경될 때 개발팀이 수기로 알람을 발송하는 과정에서 누락이 발생하는 문제를 해결한다.
CI/CD 파이프라인(Cloud Build)에서 배포 완료 후 자동으로 Swagger spec 변경을 감지하고 Google Chat으로 알람을 발송한다.

---

## 기술 스택

| 항목 | 선택 |
|---|---|
| Application | Spring Boot 4.0.6, Java 21 |
| Swagger 라이브러리 | springdoc-openapi-starter-webmvc-ui 2.8.8 |
| CI/CD | Google Cloud Build |
| API spec diff 도구 | oasdiff v1.10.14 (런타임 다운로드) |
| 알람 시스템 | Google Chat webhook |
| 스펙 스토리지 | Google Cloud Storage |
| 인프라 | GCP |

---

## 프로젝트 구조

```
swagger-diff-template/
├── cloudbuild.yaml              ← Cloud Build 파이프라인 + diff/알람 로직 전부
└── src/main/java/bacon/study/swaggerdifftemplate/
    ├── SwaggerDiffTemplateApplication.java
    ├── config/
    │   └── OpenApiConfig.java   ← springdoc-openapi 기본 정보 설정
    └── controller/
        └── SampleController.java ← Swagger 어노테이션 사용 예시
```

별도 스크립트 파일(.sh)과 커스텀 Dockerfile 없이 `cloudbuild.yaml` 단일 파일로 모든 로직을 처리한다.

---

## Spring Boot Swagger 설정

### 의존성

```kotlin
// build.gradle.kts
implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.8")
```

### Swagger 스펙 엔드포인트

springdoc-openapi 기본값 사용:

- JSON 스펙: `GET /v3/api-docs`
- Swagger UI: `GET /swagger-ui.html`

Cloud Build가 배포 후 `/v3/api-docs`에 HTTP GET 요청으로 현재 스펙을 가져온다.

---

## Cloud Build 파이프라인

### 하드코딩 값

| 항목 | 값 |
|---|---|
| GCS 버킷 | `swagger-docs` |
| 서비스명 | `swagger-diff-template` |
| dev 서버 URL | `http://[dev-server-ip]/v3/api-docs` ← 실제 IP/도메인으로 교체 필요 |
| Google Chat webhook URL | `https://chat.googleapis.com/v1/spaces/...` ← 실제 webhook URL로 교체 필요 |
| oasdiff 버전 | v1.10.14 (다운로드 URL에 고정) |
| `COMMIT_SHA` | Cloud Build 내장 변수 (`$COMMIT_SHA`) — 별도 설정 불필요 |
| `TIMESTAMP` | bash `date +%Y-%m-%dT%H%M%S` 로 생성 |

> 레포지토리가 private이므로 모두 하드코딩한다. 이후 보안 요구사항 발생 시 Secret Manager로 이전한다.

### 스텝 구성

```
Step 1: Gradle 빌드
Step 2: dev 서버 배포  (배포 방식에 따라 구현 - placeholder)
Step 3: Swagger diff + 알람 (gcr.io/google.com/cloudsdktool/cloud-sdk:slim 이미지, bash 인라인)
```

### Step 3 상세 로직

```
① oasdiff 바이너리 다운로드
② curl로 새 스펙 fetch → /workspace/new-spec.json
③ GCS에서 latest.json 다운로드 시도
   └─ 파일 없음 (첫 배포):
        - new-spec.json → gs://swagger-docs/swagger-diff-template/latest.json
        - new-spec.json → gs://swagger-docs/swagger-diff-template/{timestamp}-{commit}.json
        - Google Chat에 "최초 등록" 알람 발송
        - exit 0
④ oasdiff changelog 실행
   └─ 변경 없음: exit 0
⑤ oasdiff breaking-changes 실행
⑥ Google Chat 메시지 포맷 → webhook 전송 (최대 3회 재시도, 5초 간격)
   ├─ 성공 (HTTP 2XX):
   │    - new-spec.json → gs://swagger-docs/swagger-diff-template/latest.json (덮어쓰기)
   │    - new-spec.json → gs://swagger-docs/swagger-diff-template/{timestamp}-{commit}.json
   └─ 3회 모두 실패:
        - 에러 로그 출력
        - GCS 저장 skip (latest.json 갱신 안 함)
        - exit 0 (배포 파이프라인은 성공으로 처리)
```

### GCS 경로

```
gs://swagger-docs/swagger-diff-template/latest.json                      ← 다음 배포의 비교 기준
gs://swagger-docs/swagger-diff-template/2024-01-15T14:30:00-abc1234.json ← 이력
```

---

## Google Chat 메시지 포맷

### 변경 감지 시

```
🔔 *[swagger-diff-template] API Spec 변경 감지*

• 커밋: {COMMIT_SHA}
• 시각: {TIMESTAMP} KST

*Breaking Changes*
- DELETE /api/v1/users/{id} endpoint deleted
- ...

*Changelog*
- POST /api/v1/orders endpoint added
- ...
```

Breaking changes가 없으면 해당 섹션 생략.

### 최초 등록 시

```
📋 *[swagger-diff-template] API Spec 최초 등록*

• 커밋: {COMMIT_SHA}
• 시각: {TIMESTAMP} KST
```

---

## 엣지 케이스

| 상황 | 처리 방법 |
|---|---|
| 알람 발송 실패 | 3회 재시도(5초 간격), 최종 실패 시 로그만 출력. GCS 저장 skip. 배포는 성공으로 처리. |
| latest.json 없음 (첫 배포) | 현재 스펙을 latest.json + 타임스탬프 파일로 저장. "최초 등록" 알람 발송. |
| 변경 없음 | 알람 및 GCS 저장 없이 정상 종료. |
| 배포 환경 | dev 서버 전용. Cloud Build 트리거를 dev 브랜치에만 연결하는 방식으로 제어. |

---

## 결정 사항 및 근거

- **CI/CD 파이프라인 방식 선택**: 알람 이력 관리 및 재전송이 필수 요구사항이 아니고, webhook 방식보다 구현 복잡도가 낮기 때문.
- **커스텀 Docker 이미지 미사용**: 빌드마다 oasdiff 런타임 다운로드(약 10~20초)를 허용하고 단순한 구조를 유지.
- **하드코딩**: private 레포지토리이므로 허용. 이후 보안 요구사항 발생 시 Secret Manager 이전.
- **알람 실패 시 배포 성공 처리**: API spec 알람 누락이 비즈니스에 치명적이지 않으므로 배포 파이프라인을 막지 않음.

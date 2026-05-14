# Swagger 변경 감지 알람 시스템 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Spring Boot 앱에 springdoc-openapi Swagger 설정을 추가하고, Cloud Build 파이프라인에서 배포 후 자동으로 API spec 변경을 감지해 Google Chat으로 알람을 발송한다.

**Architecture:** Spring Boot 앱이 `/v3/api-docs`로 OpenAPI JSON을 노출한다. Cloud Build가 배포 완료 후 `gcr.io/google.com/cloudsdktool/cloud-sdk:slim` 컨테이너에서 oasdiff를 런타임 설치하고, GCS의 `latest.json`과 비교해 변경 감지 시 Google Chat webhook으로 알람을 발송한다. 알람 성공 시에만 GCS 스냅샷을 갱신한다.

**Tech Stack:** Spring Boot 4.0.6, Java 21, springdoc-openapi 2.8.8, Cloud Build, oasdiff v1.10.14, Google Chat webhook, GCS (`swagger-docs` 버킷)

---

## 파일 구조

| 파일 | 작업 |
|---|---|
| `build.gradle.kts` | springdoc-openapi 의존성 추가 |
| `src/main/java/.../config/OpenApiConfig.java` | 신규 — API title, version 설정 |
| `src/main/java/.../controller/SampleController.java` | 신규 — Swagger 어노테이션 예시 엔드포인트 |
| `src/test/java/.../SwaggerEndpointTest.java` | 신규 — `/v3/api-docs`, `/api/sample/health` 검증 |
| `cloudbuild.yaml` | 신규 — 빌드 + 배포 + diff/알람 전체 파이프라인 |

---

## 사전 조건

프로젝트 루트에서 git 초기화 (아직 안 된 경우):

```bash
git init
git add .gitignore .gitattributes build.gradle.kts settings.gradle.kts gradlew gradlew.bat gradle/ src/
git commit -m "chore: initial project structure"
```

---

## Task 1: springdoc-openapi 의존성 추가 및 /v3/api-docs 확인

**Files:**
- Modify: `build.gradle.kts`
- Create: `src/test/java/bacon/study/swaggerdifftemplate/SwaggerEndpointTest.java`

- [ ] **Step 1: 실패 테스트 작성**

```java
// src/test/java/bacon/study/swaggerdifftemplate/SwaggerEndpointTest.java
package bacon.study.swaggerdifftemplate;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class SwaggerEndpointTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void apiDocsReturns200() throws Exception {
        mockMvc.perform(get("/v3/api-docs"))
               .andExpect(status().isOk())
               .andExpect(content().contentType("application/json"));
    }
}
```

- [ ] **Step 2: 테스트 실행 → FAIL 확인**

```bash
./gradlew test --tests "bacon.study.swaggerdifftemplate.SwaggerEndpointTest.apiDocsReturns200"
```

Expected: FAIL — `Status expected:<200> but was:<404>`

- [ ] **Step 3: build.gradle.kts에 의존성 추가**

`dependencies` 블록에 아래 한 줄 추가:

```kotlin
implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.8")
```

> Spring Boot 4.x 호환 문제 발생 시: https://github.com/springdoc/springdoc-openapi/releases 에서 최신 버전 확인

- [ ] **Step 4: 테스트 실행 → PASS 확인**

```bash
./gradlew test --tests "bacon.study.swaggerdifftemplate.SwaggerEndpointTest.apiDocsReturns200"
```

Expected: PASS

- [ ] **Step 5: 커밋**

```bash
git add build.gradle.kts src/test/java/bacon/study/swaggerdifftemplate/SwaggerEndpointTest.java
git commit -m "feat: add springdoc-openapi and verify /v3/api-docs endpoint"
```

---

## Task 2: OpenApiConfig 추가

**Files:**
- Create: `src/main/java/bacon/study/swaggerdifftemplate/config/OpenApiConfig.java`
- Modify: `src/test/java/bacon/study/swaggerdifftemplate/SwaggerEndpointTest.java`

- [ ] **Step 1: API title 검증 테스트 추가**

`SwaggerEndpointTest`에 아래 메서드 추가:

```java
@Test
void apiDocsContainsTitle() throws Exception {
    mockMvc.perform(get("/v3/api-docs"))
           .andExpect(status().isOk())
           .andExpect(jsonPath("$.info.title").value("Swagger Diff Template API"));
}
```

- [ ] **Step 2: 테스트 실행 → FAIL 확인**

```bash
./gradlew test --tests "bacon.study.swaggerdifftemplate.SwaggerEndpointTest.apiDocsContainsTitle"
```

Expected: FAIL — `$.info.title` 값이 기대값과 다름

- [ ] **Step 3: OpenApiConfig.java 생성**

```java
// src/main/java/bacon/study/swaggerdifftemplate/config/OpenApiConfig.java
package bacon.study.swaggerdifftemplate.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Swagger Diff Template API")
                        .version("1.0.0")
                        .description("Template for swagger diff change notification"));
    }
}
```

- [ ] **Step 4: 전체 테스트 실행 → PASS 확인**

```bash
./gradlew test --tests "bacon.study.swaggerdifftemplate.SwaggerEndpointTest"
```

Expected: PASS (2 tests)

- [ ] **Step 5: 커밋**

```bash
git add src/main/java/bacon/study/swaggerdifftemplate/config/OpenApiConfig.java \
        src/test/java/bacon/study/swaggerdifftemplate/SwaggerEndpointTest.java
git commit -m "feat: add OpenApiConfig with service title and version"
```

---

## Task 3: SampleApiSpec 인터페이스 + SampleController 추가

Swagger 어노테이션은 `SampleApiSpec` 인터페이스에 집중하고, `SampleController`는 비즈니스 로직만 담는다.

**Files:**
- Create: `src/main/java/bacon/study/swaggerdifftemplate/controller/SampleApiSpec.java`
- Create: `src/main/java/bacon/study/swaggerdifftemplate/controller/SampleController.java`
- Modify: `src/test/java/bacon/study/swaggerdifftemplate/SwaggerEndpointTest.java`

- [ ] **Step 1: 엔드포인트 검증 테스트 추가**

`SwaggerEndpointTest`에 아래 메서드 2개 추가:

```java
@Test
void sampleHealthEndpointReturns200() throws Exception {
    mockMvc.perform(get("/api/sample/health"))
           .andExpect(status().isOk())
           .andExpect(jsonPath("$.status").value("ok"));
}

@Test
void apiDocsContainsSampleEndpoint() throws Exception {
    mockMvc.perform(get("/v3/api-docs"))
           .andExpect(status().isOk())
           .andExpect(content().string(org.hamcrest.Matchers.containsString("/api/sample/health")));
}
```

- [ ] **Step 2: 테스트 실행 → FAIL 확인**

```bash
./gradlew test --tests "bacon.study.swaggerdifftemplate.SwaggerEndpointTest.sampleHealthEndpointReturns200"
```

Expected: FAIL — `Status expected:<200> but was:<404>`

- [ ] **Step 3: SampleApiSpec.java 생성 — Swagger 어노테이션 전담 인터페이스**

```java
// src/main/java/bacon/study/swaggerdifftemplate/controller/SampleApiSpec.java
package bacon.study.swaggerdifftemplate.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.Map;

@Tag(name = "Sample", description = "Swagger diff 시연용 샘플 API")
@RequestMapping("/api/sample")
public interface SampleApiSpec {

    @Operation(summary = "헬스 체크", description = "서비스 상태를 반환한다")
    @ApiResponse(responseCode = "200", description = "서비스 정상")
    @GetMapping("/health")
    ResponseEntity<Map<String, String>> health();
}
```

- [ ] **Step 4: SampleController.java 생성 — 비즈니스 로직만**

```java
// src/main/java/bacon/study/swaggerdifftemplate/controller/SampleController.java
package bacon.study.swaggerdifftemplate.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class SampleController implements SampleApiSpec {

    @Override
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "ok"));
    }
}
```

- [ ] **Step 5: 전체 테스트 실행 → PASS 확인**

```bash
./gradlew test
```

Expected: PASS (전체 테스트 — `contextLoads` 포함 4개)

- [ ] **Step 6: 커밋**

```bash
git add src/main/java/bacon/study/swaggerdifftemplate/controller/SampleApiSpec.java \
        src/main/java/bacon/study/swaggerdifftemplate/controller/SampleController.java \
        src/test/java/bacon/study/swaggerdifftemplate/SwaggerEndpointTest.java
git commit -m "feat: add SampleApiSpec interface and SampleController"
```

---

## Task 4: cloudbuild.yaml 생성

**Files:**
- Create: `cloudbuild.yaml`

- [ ] **Step 1: cloudbuild.yaml 생성**

```yaml
steps:
  # ── Step 1: Build & Test ────────────────────────────────────
  - name: 'eclipse-temurin:21-jdk-jammy'
    entrypoint: bash
    args: ['-c', 'chmod +x gradlew && ./gradlew build']
    env: ['GRADLE_USER_HOME=/workspace/.gradle']

  # ── Step 2: Deploy ─────────────────────────────────────────
  # !! 실제 배포 방식에 맞게 교체하세요 !!
  # - name: 'gcr.io/cloud-builders/gcloud'
  #   args: ['run', 'deploy', 'swagger-diff-template', '--region=asia-northeast3', ...]

  # ── Step 3: Swagger diff + notification ────────────────────
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk:slim'
    entrypoint: bash
    args:
      - '-c'
      - |
          BUCKET="swagger-docs"
          SERVICE="swagger-diff-template"
          DEV_SERVER_URL="http://[dev-server-ip]/v3/api-docs"
          WEBHOOK="https://chat.googleapis.com/v1/spaces/[space-id]/messages?key=[key]&token=[token]"
          TIMESTAMP=$(date +%Y-%m-%dT%H%M%S)

          # oasdiff 설치
          curl -sSL "https://github.com/Tufin/oasdiff/releases/download/v1.10.14/oasdiff_Linux_x86_64.tar.gz" \
            | tar xz -C /usr/local/bin oasdiff

          # 새 스펙 fetch
          curl -sf "${DEV_SERVER_URL}" -o /workspace/new-spec.json \
            || { echo "ERROR: spec fetch 실패"; exit 0; }

          # GCS에서 이전 스펙 다운로드 (없으면 최초 배포)
          if ! gsutil cp "gs://${BUCKET}/${SERVICE}/latest.json" /workspace/old-spec.json 2>/dev/null; then
            gsutil cp /workspace/new-spec.json "gs://${BUCKET}/${SERVICE}/latest.json"
            gsutil cp /workspace/new-spec.json "gs://${BUCKET}/${SERVICE}/${TIMESTAMP}-${COMMIT_SHA}.json"
            MSG="📋 *[${SERVICE}] API Spec 최초 등록*

• 커밋: ${COMMIT_SHA}
• 시각: ${TIMESTAMP} KST"
            PAYLOAD=$(printf '%s' "${MSG}" | python3 -c "import sys,json; print(json.dumps({'text':sys.stdin.read()}))")
            curl -sf --retry 2 --retry-delay 5 --retry-all-errors \
              -X POST "${WEBHOOK}" -H "Content-Type: application/json" -d "${PAYLOAD}" || true
            exit 0
          fi

          # diff 비교
          CHANGELOG=$(oasdiff changelog /workspace/old-spec.json /workspace/new-spec.json 2>/dev/null || true)
          [ -z "${CHANGELOG}" ] && { echo "변경 없음"; exit 0; }

          BREAKING=$(oasdiff breaking-changes /workspace/old-spec.json /workspace/new-spec.json 2>/dev/null || true)

          # 메시지 구성
          MSG="🔔 *[${SERVICE}] API Spec 변경 감지*

• 커밋: ${COMMIT_SHA}
• 시각: ${TIMESTAMP} KST"
          [ -n "${BREAKING}" ] && MSG="${MSG}

*Breaking Changes*
${BREAKING}"
          MSG="${MSG}

*Changelog*
${CHANGELOG}"

          # 알람 발송 → 성공 시에만 GCS 저장
          PAYLOAD=$(printf '%s' "${MSG}" | python3 -c "import sys,json; print(json.dumps({'text':sys.stdin.read()}))")
          if curl -sf --retry 2 --retry-delay 5 --retry-all-errors \
            -X POST "${WEBHOOK}" -H "Content-Type: application/json" -d "${PAYLOAD}"; then
            gsutil cp /workspace/new-spec.json "gs://${BUCKET}/${SERVICE}/latest.json"
            gsutil cp /workspace/new-spec.json "gs://${BUCKET}/${SERVICE}/${TIMESTAMP}-${COMMIT_SHA}.json"
          else
            echo "ERROR: 알람 발송 실패, GCS 저장 skip"
          fi

          exit 0

timeout: '1200s'
options:
  logging: CLOUD_LOGGING_ONLY
```

- [ ] **Step 2: YAML 문법 검증**

```bash
python3 -c "import yaml; yaml.safe_load(open('cloudbuild.yaml')); print('YAML syntax OK')"
```

Expected: `YAML syntax OK`

- [ ] **Step 3: 실제 값으로 교체**

`cloudbuild.yaml` 내 아래 두 줄을 실제 환경 값으로 수정:

```
DEV_SERVER_URL="http://[dev-server-ip]/v3/api-docs"
              ↓
DEV_SERVER_URL="http://실제-dev-서버-ip-또는-도메인/v3/api-docs"

GOOGLE_CHAT_WEBHOOK="https://chat.googleapis.com/v1/spaces/[space-id]/messages?key=[key]&token=[token]"
              ↓
GOOGLE_CHAT_WEBHOOK="Google Chat에서 발급받은 실제 webhook URL"
```

- [ ] **Step 4: 커밋**

```bash
git add cloudbuild.yaml
git commit -m "feat: add cloudbuild pipeline with swagger diff and Google Chat notification"
```

---

## 참고: oasdiff 아카이브 내 바이너리명 확인

`tar xz -C /usr/local/bin oasdiff` 명령은 아카이브 안에 `oasdiff`라는 이름의 파일이 있다고 가정한다.
만약 Cloud Build 실행 시 `oasdiff: Not found in archive` 에러가 발생하면 아래로 아카이브 내용 확인:

```bash
curl -sSL "https://github.com/Tufin/oasdiff/releases/download/v1.10.14/oasdiff_Linux_x86_64.tar.gz" \
  | tar tz
```

바이너리명이 다르면 `tar xz -C /usr/local/bin oasdiff` 의 마지막 인자를 실제 파일명으로 수정.

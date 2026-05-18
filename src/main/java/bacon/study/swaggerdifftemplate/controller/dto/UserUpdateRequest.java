package bacon.study.swaggerdifftemplate.controller.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "회원 정보 수정 요청")
public record UserUpdateRequest(
        @Schema(description = "이름", example = "홍길동")
        String name,

        @Schema(description = "이메일", example = "hong@example.com")
        String email,

        @Schema(description = "전화번호", example = "010-1234-5678")
        String phone
) {}

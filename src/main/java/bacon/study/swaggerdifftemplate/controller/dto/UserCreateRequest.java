package bacon.study.swaggerdifftemplate.controller.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "회원가입 요청")
public record UserCreateRequest(
        @Schema(description = "이름", example = "홍길동", requiredMode = Schema.RequiredMode.REQUIRED)
        String name,

        @Schema(description = "이메일", example = "hong@example.com", requiredMode = Schema.RequiredMode.REQUIRED)
        String email,

        @Schema(description = "비밀번호", example = "password1234", requiredMode = Schema.RequiredMode.REQUIRED)
        String password,

        @Schema(description = "전화번호", example = "010-1234-5678")
        String phone
) {}

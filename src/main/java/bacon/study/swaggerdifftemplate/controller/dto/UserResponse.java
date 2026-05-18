package bacon.study.swaggerdifftemplate.controller.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "회원 응답")
public record UserResponse(
        @Schema(description = "회원 ID", example = "1")
        Long id,

        @Schema(description = "이름", example = "홍길동")
        String name,

        @Schema(description = "이메일", example = "hong@example.com")
        String email,

        @Schema(description = "역할", example = "USER")
        String role
) {}

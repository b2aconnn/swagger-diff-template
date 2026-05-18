package bacon.study.swaggerdifftemplate.controller.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "에러 응답")
public record ErrorResponse(
        @Schema(description = "에러 코드", example = "USER_NOT_FOUND")
        String code,

        @Schema(description = "에러 메시지", example = "해당 회원을 찾을 수 없습니다.")
        String message
) {}

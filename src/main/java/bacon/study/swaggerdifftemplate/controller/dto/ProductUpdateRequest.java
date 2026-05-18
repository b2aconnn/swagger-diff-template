package bacon.study.swaggerdifftemplate.controller.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "상품 수정 요청")
public record ProductUpdateRequest(
        @Schema(description = "상품명", example = "MacBook Air")
        String name,

        @Schema(description = "가격", example = "1800000")
        Integer price,

        @Schema(description = "재고 수량", example = "50")
        Integer stock
) {}

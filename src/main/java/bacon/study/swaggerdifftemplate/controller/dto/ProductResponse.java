package bacon.study.swaggerdifftemplate.controller.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "상품 응답")
public record ProductResponse(
        @Schema(description = "상품 ID", example = "1")
        Long id,

        @Schema(description = "상품명", example = "MacBook Pro")
        String name,

        @Schema(description = "가격", example = "2500000")
        Integer price,

        @Schema(description = "재고 수량", example = "100")
        Integer stock,

        @Schema(description = "카테고리", example = "전자제품")
        String category
) {}

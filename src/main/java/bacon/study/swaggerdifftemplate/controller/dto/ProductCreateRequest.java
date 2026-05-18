package bacon.study.swaggerdifftemplate.controller.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "상품 등록 요청")
public record ProductCreateRequest(
        @Schema(description = "상품명", example = "MacBook Pro", requiredMode = Schema.RequiredMode.REQUIRED)
        String name,

        @Schema(description = "가격", example = "2500000", requiredMode = Schema.RequiredMode.REQUIRED)
        Integer price,

        @Schema(description = "재고 수량", example = "100")
        Integer stock
) {}

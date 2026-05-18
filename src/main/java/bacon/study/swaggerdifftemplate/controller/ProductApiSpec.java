package bacon.study.swaggerdifftemplate.controller;

import bacon.study.swaggerdifftemplate.controller.dto.ErrorResponse;
import bacon.study.swaggerdifftemplate.controller.dto.ProductCreateRequest;
import bacon.study.swaggerdifftemplate.controller.dto.ProductResponse;
import bacon.study.swaggerdifftemplate.controller.dto.ProductUpdateRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;

import java.util.List;

@Tag(name = "Product", description = "상품 관리 API")
public interface ProductApiSpec {

    @Operation(summary = "상품 목록 조회")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "조회 성공",
                    content = @Content(schema = @Schema(implementation = ProductResponse.class)))
    })
    ResponseEntity<List<ProductResponse>> getProducts();

    @Operation(summary = "상품 상세 조회")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "조회 성공",
                    content = @Content(schema = @Schema(implementation = ProductResponse.class))),
            @ApiResponse(responseCode = "404", description = "상품 없음",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    ResponseEntity<ProductResponse> getProduct(
            @Parameter(description = "상품 ID", required = true) Long id
    );

    @Operation(summary = "상품 등록")
    @ApiResponses({
            @ApiResponse(responseCode = "201", description = "등록 성공",
                    content = @Content(schema = @Schema(implementation = ProductResponse.class))),
            @ApiResponse(responseCode = "400", description = "잘못된 요청",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    ResponseEntity<ProductResponse> createProduct(ProductCreateRequest request);

    @Operation(summary = "상품 수정")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "수정 성공",
                    content = @Content(schema = @Schema(implementation = ProductResponse.class))),
            @ApiResponse(responseCode = "400", description = "잘못된 요청",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "404", description = "상품 없음",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    ResponseEntity<ProductResponse> updateProduct(
            @Parameter(description = "상품 ID", required = true) Long id,
            ProductUpdateRequest request
    );

    @Operation(summary = "상품 삭제")
    @ApiResponses({
            @ApiResponse(responseCode = "204", description = "삭제 성공"),
            @ApiResponse(responseCode = "404", description = "상품 없음",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    ResponseEntity<Void> deleteProduct(
            @Parameter(description = "상품 ID", required = true) Long id
    );
}

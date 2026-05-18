package bacon.study.swaggerdifftemplate.controller;

import bacon.study.swaggerdifftemplate.controller.dto.ProductCreateRequest;
import bacon.study.swaggerdifftemplate.controller.dto.ProductResponse;
import bacon.study.swaggerdifftemplate.controller.dto.ProductUpdateRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/products")
public class ProductController implements ProductApiSpec {

    @Override
    @GetMapping
    public ResponseEntity<List<ProductResponse>> getProducts(
            @RequestParam(defaultValue = "0") Integer page,
            @RequestParam(defaultValue = "20") Integer size) {
        return ResponseEntity.ok(List.of(
                new ProductResponse(1L, "MacBook Pro", 2500000, 100, "전자제품"),
                new ProductResponse(2L, "iPhone 15", 1200000, 200, "전자제품")
        ));
    }

    @Override
    @GetMapping("/{id}")
    public ResponseEntity<ProductResponse> getProduct(@PathVariable Long id) {
        return ResponseEntity.ok(new ProductResponse(id, "MacBook Pro", 2500000, 100, "전자제품"));
    }

    @Override
    @PostMapping
    public ResponseEntity<ProductResponse> createProduct(@RequestBody ProductCreateRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(new ProductResponse(1L, request.name(), request.price(), request.stock(), null));
    }

    @Override
    @PutMapping("/{id}")
    public ResponseEntity<ProductResponse> updateProduct(@PathVariable Long id, @RequestBody ProductUpdateRequest request) {
        return ResponseEntity.ok(new ProductResponse(id, request.name(), request.price(), request.stock(), null));
    }

    @Override
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable Long id) {
        return ResponseEntity.noContent().build();
    }
}

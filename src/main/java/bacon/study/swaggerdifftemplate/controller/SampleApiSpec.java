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

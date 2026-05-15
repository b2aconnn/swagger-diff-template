package bacon.study.swaggerdifftemplate.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;

import java.util.Map;

@Tag(name = "User", description = "회원 관리 API")
public interface UserApiSpec {

    @Operation(summary = "회원 정보 조회")
    @ApiResponse(responseCode = "200", description = "조회 성공")
    ResponseEntity<Map<String, Object>> getUser(@Parameter(description = "회원 ID") Long id);

    @Operation(summary = "회원가입")
    @ApiResponse(responseCode = "201", description = "가입 성공")
    ResponseEntity<Map<String, Object>> createUser(Map<String, Object> request);

    @Operation(summary = "회원 정보 수정")
    @ApiResponse(responseCode = "200", description = "수정 성공")
    ResponseEntity<Map<String, Object>> updateUser(@Parameter(description = "회원 ID") Long id, Map<String, Object> request);

    @Operation(summary = "회원 삭제")
    @ApiResponse(responseCode = "204", description = "삭제 성공")
    ResponseEntity<Void> deleteUser(@Parameter(description = "회원 ID") Long id);
}

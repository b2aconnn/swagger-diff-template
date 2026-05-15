package bacon.study.swaggerdifftemplate.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/users")
public class UserController implements UserApiSpec {

    @Override
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(Map.of("id", id, "name", "홍길동", "email", "test@test.com"));
    }

    @Override
    @PostMapping
    public ResponseEntity<Map<String, Object>> createUser(@RequestBody Map<String, Object> request) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(Map.of("id", 1, "name", request.getOrDefault("name", ""), "email", request.getOrDefault("email", "")));
    }

    @Override
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateUser(@PathVariable Long id, @RequestBody Map<String, Object> request) {
        return ResponseEntity.ok(Map.of("id", id, "name", request.getOrDefault("name", ""), "email", request.getOrDefault("email", "")));
    }

    @Override
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        return ResponseEntity.noContent().build();
    }
}

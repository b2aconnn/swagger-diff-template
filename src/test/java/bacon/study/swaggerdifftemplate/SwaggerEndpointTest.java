package bacon.study.swaggerdifftemplate;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class SwaggerEndpointTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void apiDocsReturns200() throws Exception {
        mockMvc.perform(get("/v3/api-docs"))
               .andExpect(status().isOk())
               .andExpect(content().contentType("application/json"));
    }

    @Test
    void apiDocsContainsTitle() throws Exception {
        mockMvc.perform(get("/v3/api-docs"))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.info.title").value("Swagger Diff Template API"));
    }
}

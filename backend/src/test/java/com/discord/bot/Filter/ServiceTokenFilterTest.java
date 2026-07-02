package com.discord.bot.Filter;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

class ServiceTokenFilterTest {
    private static final String SERVICE_TOKEN = "secret-token";

    private final ServiceTokenFilter filter = new ServiceTokenFilter(SERVICE_TOKEN);

    @AfterEach
    void tearDown() {
        SecurityContextHolder.clearContext();
    }

    @Test
    void skipsHealthEndpointWithoutAuthorization() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/actuator/health");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);

        filter.doFilter(request, response, (servletRequest, servletResponse) -> chainCalled.set(true));

        assertTrue(chainCalled.get());
        assertEquals(200, response.getStatus());
    }

    @Test
    void skipsPublicImageFileGetWithoutAuthorization() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/images/123/file");
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicBoolean chainCalled = new AtomicBoolean(false);

        filter.doFilter(request, response, (servletRequest, servletResponse) -> chainCalled.set(true));

        assertTrue(chainCalled.get());
        assertEquals(200, response.getStatus());
    }

    @ParameterizedTest
    @ValueSource(strings = { "", "Basic abc", "Bearer wrong-token" })
    void rejectsMissingMalformedAndWrongBearerTokens(String authorizationHeader) throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/images/all");
        if (!authorizationHeader.isEmpty()) {
            request.addHeader("Authorization", authorizationHeader);
        }
        MockHttpServletResponse response = new MockHttpServletResponse();

        filter.doFilter(request, response, (servletRequest, servletResponse) -> fail("chain should not be called"));

        assertEquals(401, response.getStatus());
        assertEquals("application/json", response.getContentType());
        assertEquals("{\"error\":\"Unauthorized\"}", response.getContentAsString());
        assertNull(SecurityContextHolder.getContext().getAuthentication());
    }

    @Test
    void acceptsValidBearerTokenAndClearsAuthenticationAfterChain() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/images/123/vote");
        request.addHeader("Authorization", "Bearer " + SERVICE_TOKEN);
        MockHttpServletResponse response = new MockHttpServletResponse();
        AtomicReference<Authentication> authenticationDuringChain = new AtomicReference<>();

        filter.doFilter(
                request,
                response,
                (servletRequest, servletResponse) -> authenticationDuringChain
                        .set(SecurityContextHolder.getContext().getAuthentication()));

        Authentication authentication = authenticationDuringChain.get();
        assertEquals("bot", authentication.getName());
        assertTrue(authentication.getAuthorities().stream()
                .anyMatch(authority -> "ROLE_BOT".equals(authority.getAuthority())));
        assertNull(SecurityContextHolder.getContext().getAuthentication());
        assertEquals(200, response.getStatus());
    }
}

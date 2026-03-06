package com.discord.bot.Filter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import io.github.bucket4j.Bucket;
import io.github.bucket4j.Bandwidth;
import io.github.bucket4j.Refill;
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

public class RateLimitFilter implements jakarta.servlet.Filter {
    private static final Logger log = LoggerFactory.getLogger(RateLimitFilter.class);

    private final Cache<String, Bucket> cache = Caffeine.newBuilder()
            .maximumSize(1000)
            .expireAfterAccess(10, TimeUnit.MINUTES)
            .build();

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws java.io.IOException, ServletException {
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.isAuthenticated()) {
            chain.doFilter(request, response);
            return;
        }
        String key = httpRequest.getHeader("X-User-Id");
        String name = httpRequest.getHeader("X-User-Name");
        if (key == null) {
            key = httpRequest.getRemoteAddr();
        }
        if (name == null) {
            name = "Unknown";
        }

        Bucket bucket = cache.get(key, k -> createBucket());
        long availableTokens = bucket.getAvailableTokens();
        log.debug("UserID: {} || username= {} has {} tokens left.", key, name, availableTokens);
        if (bucket.tryConsume(1)) {
            chain.doFilter(request, response);
        } else {
            HttpServletResponse httpResponse = (HttpServletResponse) response;
            httpResponse.setStatus(429);
            httpResponse.setContentType("application/json");
            httpResponse.getWriter().write("{\"error\": \"Too many requests\"}");
        }
    }

    public Bucket createBucket() {
        Bandwidth limit = Bandwidth.classic(80, Refill.greedy(80, Duration.ofMinutes(1)));
        return Bucket.builder()
                .addLimit(limit)
                .build();
    }
}

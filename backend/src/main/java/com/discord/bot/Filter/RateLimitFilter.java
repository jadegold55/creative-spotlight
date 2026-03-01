package com.discord.bot.Filter;

import jakarta.servlet.Filter;
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
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;

@Component
public class RateLimitFilter implements jakarta.servlet.Filter {
    @Value("${bot.secret}")
    private String expectedBotId;

    private final Cache<String, Bucket> cache = Caffeine.newBuilder()
            .maximumSize(1000)
            .expireAfterAccess(10, TimeUnit.MINUTES)
            .build();

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws java.io.IOException, ServletException {
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        try {
            java.util.Enumeration<String> names = httpRequest.getHeaderNames();
            while (names.hasMoreElements()) {
                String name = names.nextElement();
                System.out.println("DEBUG  " + name + " = " + httpRequest.getHeader(name));
            }

            String bot = httpRequest.getHeader("Bot-User-Id");
            if (bot != null && bot.equals(expectedBotId)) {
                System.out.println("Request from bot " + bot + " is allowed.");
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
            System.out
                    .println("UserID: " + key + " || username= " + name + " has " + availableTokens + " tokens left.");
            if (bucket.tryConsume(1)) {
                chain.doFilter(request, response);
            } else {
                HttpServletResponse httpResponse = (HttpServletResponse) response;
                httpResponse.setStatus(429);
                httpResponse.setContentType("application/json");
                httpResponse.getWriter().write("{\"error\": \"Too many requests\"}");
            }
        } catch (Exception e) {
            HttpServletResponse httpResponse = (HttpServletResponse) response;
            httpResponse.setStatus(500);
            httpResponse.setContentType("application/json");
            httpResponse.getWriter().write("{\"error\": \"Internal server error\"}");
        }
    }

    public Bucket createBucket() {
        Bandwidth limit = Bandwidth.classic(30, Refill.greedy(30, Duration.ofMinutes(1)));
        return Bucket.builder()
                .addLimit(limit)
                .build();
    }
}

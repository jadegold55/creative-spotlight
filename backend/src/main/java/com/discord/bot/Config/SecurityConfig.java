package com.discord.bot.Config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.Customizer;
import com.discord.bot.Filter.RateLimitFilter;
import com.discord.bot.Filter.ServiceTokenFilter;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    private final RateLimitFilter rateLimitFilter;
    private final ServiceTokenFilter serviceTokenFilter;

    public SecurityConfig(RateLimitFilter rateLimitFilter, ServiceTokenFilter serviceTokenFilter) {
        this.rateLimitFilter = rateLimitFilter;
        this.serviceTokenFilter = serviceTokenFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers(HttpMethod.GET, "/images/*/file").permitAll()
                        .anyRequest().authenticated())
                .httpBasic(Customizer.withDefaults())
                .addFilterBefore(serviceTokenFilter, UsernamePasswordAuthenticationFilter.class)
                .addFilterBefore(rateLimitFilter, org.springframework.web.filter.CorsFilter.class);

        return http.build();
    }
}
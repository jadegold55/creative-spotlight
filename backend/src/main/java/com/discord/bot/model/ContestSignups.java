
package com.discord.bot.model;

import java.time.Instant;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;

@Table(name = "contest_signups", uniqueConstraints = {
        @UniqueConstraint(name = "uk_contest_signup_guild_user", columnNames = { "guild_id", "user_id" })
})
@Entity
public class ContestSignups {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "guild_id", nullable = false)
    private Long guildId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "username", nullable = false)
    private String username;

    @Column(name = "is_verified", nullable = false)
    private boolean isVerified;

    @Column(name = "signup_deadline_at", nullable = false)
    private Instant signupDeadlineAt;

    public ContestSignups() {
    }

    public ContestSignups(Long userId, Long guildId, String username, boolean isVerified, Instant signupDeadlineAt) {
        this.userId = userId;
        this.guildId = guildId;
        this.username = username;
        this.isVerified = isVerified;
        this.signupDeadlineAt = signupDeadlineAt;
    }

    public Long getGuildId() {
        return guildId;
    }

    public Long getId() {
        return id;
    }

    public Long getUserId() {
        return userId;
    }

    public String getUsername() {
        return username;
    }

    public boolean isVerified() {
        return isVerified;
    }

    public Instant getSignupDeadlineAt() {
        return signupDeadlineAt;
    }

}

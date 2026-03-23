package com.discord.bot.model;

import java.time.Instant;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity

public class GuildSettings {
    @Id
    private Long guildId;
    @Column(name = "spotlight_channel_id")
    private Long spotlightChannelId;
    @Column(name = "poem_channel_id")
    private Long poemChannelId;
    @Column(name = "poem_hour")
    private Integer poemHour;
    @Column(name = "poem_minute")
    private Integer poemMinute;
    @Column(name = "poem_timezone")
    private String poemTimezone;
    @Column(name = "contest_start_at")
    private Instant contestStartAt;
    @Column(name = "contest_deadline_at")
    private Instant contestDeadlineAt;

    public GuildSettings() {

    }

    public GuildSettings(Long guildId, Long spotlightChannelId, Long poemChannelId) {
        this.guildId = guildId;
        this.spotlightChannelId = spotlightChannelId;
        this.poemChannelId = poemChannelId;
    }

    // Getters
    public Long getGuildId() {
        return guildId;
    }

    public Long getSpotlightChannelId() {
        return spotlightChannelId;
    }

    public Long getPoemChannelId() {
        return poemChannelId;
    }

    public Integer getPoemHour() {
        return poemHour;
    }

    public Integer getPoemMinute() {
        return poemMinute;
    }

    public String getPoemTimezone() {
        return poemTimezone;
    }

    public Instant getContestStartAt() {
        return contestStartAt;
    }

    public Instant getContestDeadlineAt() {
        return contestDeadlineAt;
    }

    // Setters
    public void setGuildId(Long guildId) {
        this.guildId = guildId;
    }

    public void setSpotlightChannelId(Long spotlightChannelId) {
        this.spotlightChannelId = spotlightChannelId;
    }

    public void setPoemChannelId(Long poemChannelId) {
        this.poemChannelId = poemChannelId;
    }

    public void setPoemHour(Integer poemHour) {
        this.poemHour = poemHour;
    }

    public void setPoemMinute(Integer poemMinute) {
        this.poemMinute = poemMinute;
    }

    public void setPoemTimezone(String poemTimezone) {
        this.poemTimezone = poemTimezone;
    }

    public void setContestStartAt(Instant contestStartAt) {
        this.contestStartAt = contestStartAt;
    }

    public void setContestDeadlineAt(Instant contestDeadlineAt) {
        this.contestDeadlineAt = contestDeadlineAt;
    }
}
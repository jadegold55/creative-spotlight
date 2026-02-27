package com.discord.bot.model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Column;

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
    @Column(name = "contest_day")
    private Integer contestDay;
    @Column(name = "contest_hour")
    private Integer contestHour;
    @Column(name = "contest_minute")
    private Integer contestMinute;
    @Column(name = "contest_timezone")
    private String contestTimeZone;
    @Column(name = "contest_duration_days")
    private Integer contestDurationDays;

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

    public Integer getContestDay() {
        return contestDay;
    }

    public Integer getContestHour() {
        return contestHour;
    }

    public Integer getContestMinute() {
        return contestMinute;
    }

    public String getContestTimezone() {
        return contestTimeZone;
    }

    public Integer getContestDurationDays() {
        return contestDurationDays;
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

    public void setContestDay(Integer contestDay) {
        this.contestDay = contestDay;
    }

    public void setContestHour(Integer contestHour) {
        this.contestHour = contestHour;
    }

    public void setContestMinute(Integer contestMinute) {
        this.contestMinute = contestMinute;
    }

    public void setContestTimezone(String contestTimezone) {
        this.contestTimeZone = contestTimezone;
    }

    public void setContestDurationDays(Integer contestDurationDays) {
        this.contestDurationDays = contestDurationDays;
    }
}
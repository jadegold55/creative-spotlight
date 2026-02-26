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

    public GuildSettings() {

    }

    public GuildSettings(Long guildId, Long spotlightChannelId, Long poemChannelId) {
        this.guildId = guildId;
        this.spotlightChannelId = spotlightChannelId;
        this.poemChannelId = poemChannelId;
    }

    public Long getGuildId() {
        return guildId;
    }

    public void setGuildId(Long guildId) {
        this.guildId = guildId;
    }

    public Long getSpotlightChannelId() {
        return spotlightChannelId;
    }

    public void setSpotlightChannelId(Long spotlightChannelId) {
        this.spotlightChannelId = spotlightChannelId;
    }

    public Long getPoemChannelId() {
        return poemChannelId;
    }

    public void setPoemChannelId(Long poemChannelId) {
        this.poemChannelId = poemChannelId;
    }
}
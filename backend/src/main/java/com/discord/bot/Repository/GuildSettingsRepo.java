package com.discord.bot.Repository;

import com.discord.bot.model.GuildSettings;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface GuildSettingsRepo extends JpaRepository<GuildSettings, Long> {

    List<GuildSettings> findBySpotlightChannelIdIsNotNull();

    List<GuildSettings> findByPoemChannelIdIsNotNull();

}

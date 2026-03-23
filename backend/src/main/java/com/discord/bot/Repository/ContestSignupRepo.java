package com.discord.bot.Repository;

import java.time.Instant;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.discord.bot.model.ContestSignups;

public interface ContestSignupRepo extends JpaRepository<ContestSignups, Long> {

	List<ContestSignups> findByGuildIdOrderByUsernameAsc(Long guildId);

	boolean existsByGuildIdAndUserId(Long guildId, Long userId);

	long deleteByGuildIdAndUserId(Long guildId, Long userId);

	long deleteByGuildIdAndSignupDeadlineAtLessThanEqual(Long guildId, Instant signupDeadlineAt);

}

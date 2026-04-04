package com.discord.bot.Repository;

import java.time.Instant;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.discord.bot.model.ContestSignups;

public interface ContestSignupRepo extends JpaRepository<ContestSignups, Long> {

	List<ContestSignups> findByGuildIdOrderByUsernameAsc(Long guildId);

	List<ContestSignups> findByGuildIdAndSignupDeadlineAtOrderByUsernameAsc(Long guildId, Instant signupDeadlineAt);

	boolean existsByGuildIdAndUserId(Long guildId, Long userId);

	boolean existsByGuildIdAndUserIdAndSignupDeadlineAt(Long guildId, Long userId, Instant signupDeadlineAt);

	List<ContestSignups> findByGuildIdAndSignupDeadlineAt(Long guildId, Instant signupDeadlineAt);

	long deleteByGuildIdAndUserId(Long guildId, Long userId);

	long deleteByGuildIdAndUserIdAndSignupDeadlineAt(Long guildId, Long userId, Instant signupDeadlineAt);

	long deleteByGuildIdAndSignupDeadlineAtLessThanEqual(Long guildId, Instant signupDeadlineAt);

	long deleteByGuildIdAndSignupDeadlineAtLessThan(Long guildId, Instant signupDeadlineAt);

}

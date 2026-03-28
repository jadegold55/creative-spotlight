package com.discord.bot.Repository;

import com.discord.bot.model.Poem;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import com.discord.bot.model.PoemVote;

public interface PoemVoteRepo extends JpaRepository<PoemVote, Long> {
    Optional<PoemVote> findByUserIdAndPoem(Long userId, Poem poem);

    Long countByPoem(Poem poem);
}

package com.discord.bot.Repository;

import com.discord.bot.model.Poem;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import com.discord.bot.model.PoemVote;

public interface PoemVoteRepo extends JpaRepository<PoemVote, Long> {
    public Optional<PoemVote> findByUserIDAndPoem(Long userID, Poem poem);

    public Long countByPoem(Poem poem);
}

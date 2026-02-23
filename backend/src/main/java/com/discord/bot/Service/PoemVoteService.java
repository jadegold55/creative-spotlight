package com.discord.bot.Service;

import org.springframework.stereotype.Service;
import com.discord.bot.Exceptions.InvalidVote;
import com.discord.bot.Repository.PoemVoteRepo;
import com.discord.bot.model.PoemVote;
import com.discord.bot.model.Poem;

@Service
public class PoemVoteService {
    private final PoemVoteRepo poemVoteRepo;

    public PoemVoteService(PoemVoteRepo poemVoteRepo) {
        this.poemVoteRepo = poemVoteRepo;
    }

    public void addVote(Long userID, Poem poem) {
        if (poemVoteRepo.findByUserIDAndPoem(userID, poem).isPresent()) {
            throw new InvalidVote("Unique ID must have Unique Poem ID");
        }
        poemVoteRepo.save(new PoemVote(userID, poem));
    }

    public Long getVoteCount(Poem poem) {
        return poemVoteRepo.countByPoem(poem);
    }
}

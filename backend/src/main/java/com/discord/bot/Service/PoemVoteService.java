package com.discord.bot.Service;

import org.springframework.stereotype.Service;
import com.discord.bot.Exceptions.InvalidVote;
import com.discord.bot.Repository.PoemVoteRepo;
import com.discord.bot.model.PoemVote;
import com.discord.bot.model.Poem;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;

@Service
public class PoemVoteService {
    @Autowired
    private PoemVoteRepo poemrepo;

    public void addVote(Long userID, Poem poem) {
        Optional<PoemVote> existingVote = poemrepo.findByUserIDAndPoem(userID, poem);
        if (existingVote.isPresent()) {
            throw new InvalidVote("Unique ID must have Unique Poem ID");
        } else {
            poemrepo.save(new PoemVote(userID, poem));
        }
    }

    public Long getVoteCount(Poem poem) {
        return poemrepo.countByPoem(poem);
    }
}

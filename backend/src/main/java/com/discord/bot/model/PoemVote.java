package com.discord.bot.model;

import java.lang.annotation.Inherited;
import com.discord.bot.model.Poem;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Table;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.UniqueConstraint;

@Entity
@Table(name = "PoemVote", uniqueConstraints = {
        @UniqueConstraint(name = "Unique_Person_and_Unique_Poem", columnNames = { "poem_id", "userID" })
})
public class PoemVote {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @ManyToOne
    private Poem poem;
    private Long userID;

    public PoemVote(Long user, Poem poem) {
        this.userID = user;
        this.poem = poem;
    }

    public PoemVote() {
    }
}

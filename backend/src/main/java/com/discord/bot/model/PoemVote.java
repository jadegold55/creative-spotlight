package com.discord.bot.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Table;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.UniqueConstraint;

@Entity
@Table(name = "PoemVote", uniqueConstraints = {
        @UniqueConstraint(name = "Unique_Person_and_Unique_Poem", columnNames = { "poem_id", "user_id" })
})
public class PoemVote {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @ManyToOne
    private Poem poem;
    @Column(name = "user_id")
    private Long userId;

    public PoemVote(Long userId, Poem poem) {
        this.userId = userId;
        this.poem = poem;
    }

    public PoemVote() {
    }
}

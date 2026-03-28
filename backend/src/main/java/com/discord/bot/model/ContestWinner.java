package com.discord.bot.model;

public class ContestWinner {
    private Long id;
    private Long uploaderId;
    private Long votes;

    public ContestWinner(Long id, Long uploaderId, Long votes) {
        this.id = id;
        this.uploaderId = uploaderId;
        this.votes = votes;
    }

    public Long getId() {
        return id;
    }

    public Long getUploaderId() {
        return uploaderId;
    }

    public Long getVotes() {
        return votes;
    }
}

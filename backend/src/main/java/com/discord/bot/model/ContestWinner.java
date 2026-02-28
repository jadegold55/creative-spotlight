package com.discord.bot.model;

public class ContestWinner {
    private Long id;
    private Long uploaderid;
    private Long votes;

    public ContestWinner(Long id, Long uploaderid, Long votes) {
        this.id = id;
        this.uploaderid = uploaderid;
        this.votes = votes;
    }

    public Long getId() {
        return id;
    }

    public Long getUploaderid() {
        return uploaderid;
    }

    public Long getVotes() {
        return votes;
    }
}

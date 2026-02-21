package com.discord.bot.Exceptions;

public class InvalidVote extends RuntimeException {
    public InvalidVote(String message) {
        super(message);
    }
}

package com.discord.bot.Exceptions;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import com.discord.bot.Exceptions.InvalidVote;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(InvalidVote.class)
    public ResponseEntity<String> handleInvalidVoteException(InvalidVote ex) {

        return new ResponseEntity<>(ex.getMessage(), HttpStatus.CONFLICT);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<String> handleGenericException(Exception ex) {

        return new ResponseEntity<>("An unexpected error occurred", HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
package com.discord.bot.Repository;

import com.discord.bot.model.Poem;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PoemRepo extends JpaRepository<Poem, Long> {

}

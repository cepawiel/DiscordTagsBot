const Discord = require('discord.js');
const client = new Discord.Client();

function addReactionListeners(msg){
     // add reaction listeners
     const filter = (reaction, user) => {
         if(user.id === reaction.message.guild.me.id) {4
             return false;
         }
         if(reaction.message.channel.name !== "tags") {
             return false;
         }
         return true;
     };

     const collector = msg.createReactionCollector(filter, { dispose: true });

     collector.on('collect', (reaction, user) => {
         // add roles to user
         reaction.message.mentions.roles.forEach( (role, id) => {
             console.log("Adding " + role.name + " to " + user.tag);
             msg.guild.member(user.id).roles.add(role);
         });
     });

     collector.on('remove', (reaction, user) => {
         // remove roles from user
         reaction.message.mentions.roles.forEach( (role, id) => {
             console.log("Removing " + role.name + " from " + user.tag);
             msg.guild.member(user.id).roles.remove(role);
         });
     });
};

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);

    client.guilds.cache.forEach(guild => {
        console.log("Loading from " + guild.name);

        guild.roles.fetch().then(roles => {
            // Find bot role
            let botRole = guild.roles.cache.find(role => role.name === guild.me.displayName);
            if(botRole == undefined) {
                console.log("Couldnt Find Bot Role");
                return;
            }

            // find tags channel
            guild.channels.cache.forEach(channel => {
                if(channel.name === "tags" && channel.type === "text"){
                    console.log("Found tags channel in " + guild.name);
                    
                    // check for each role
                    guild.roles.cache.forEach( (role, roleid) => {
                        // check if role is above bots role and not @everyone
                        // so we dont create messages for normal roles
                        if (role.rawPosition >= botRole.rawPosition){
                            return;
                        }

                        if (role.name == "@everyone")
                            return;

                        console.log("Found role: " + role.name);
                        // check each message for role
                        channel.messages.fetch().then(messages => {
                            match = false
                            messages.forEach(msg => {
                                // if no mentions
                                if (msg.mentions.roles.size == 0) 
                                    return;

                                msg.mentions.roles.forEach( (msgrole, msgroleid) => {
                                    // check if role matches message
                                    if(role === msgrole){
                                        console.log("Found match for " + role.name);
                                        msg.react('👍');
                                        match = true

                                        addReactionListeners(msg);

                                        // clear members from roll
                                        console.log("Removing users from " + role.name);
                                        role.members.forEach(guildmember => {
                                                guild.member(guildmember.id).roles.remove(role).catch(console.error);
                                        });

                                        msg.reactions.cache.forEach(react => {
                                            react.users.fetch().then(users => {
                                                users.forEach(user => {
                                                    // skip if me
                                                    if (user.id === guild.me.id) {
                                                        return;
                                                    }

                                                    console.log("Adding User " + user.tag +  " to " + role.name);
                                                    guild.members.fetch(user.id).then(guildmember => {
                                                        guildmember.roles.add(role).catch(console.error);
                                                    });
                                                });
                                            });
                                        });
                                    } 
                                });                        
                            });
                            
                            // Create message if necessary
                            if(match === false) {
                                console.log("Creating message for " + role.name);  
                                channel.send("<@&" + role.id + ">").then(msg => {
                                    msg.react('👍');
                                    addReactionListeners(msg);
                                });
                            }
                        }).catch(err => {
                            console.log(err);
                        });
                    });   
                }
            });

        });
    });
    return;
});

console.log(Discord.version);

min = process.env.RUNTIME;
sec =  min * 60;
ms = sec * 1000;
console.log("Running for " + ms + "ms");
client.login(process.env.DISCORD_APIKEY);
// setTimeout( () => {
//     console.log("Closing Client");
//     client.destroy();
// }, ms);
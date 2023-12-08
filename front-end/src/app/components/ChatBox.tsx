"use client"

import styles from '../page.module.css' 
import Image from 'next/image'
import React, { useState } from 'react'
import { v4 as uuidv4 } from 'uuid';

import ChatMessage from './ChatMessage'

interface messageItem {
    sender: string,
    message: string,
  }

function ChatBox() {
    const [messages, setMessages] = useState<messageItem[] | []>([])

    const messageList = messages.map((messageToDisplay) =>
        <ChatMessage key = {uuidv4()} sender = {messageToDisplay.sender} message = {messageToDisplay.message}/>
    )

    const handleSendMessage = () => {
      const messageBox = document.getElementById("inputMessage") as HTMLInputElement
      if (messageBox) {
        const inputMessage = messageBox.value
        const newMessage: messageItem = {
          sender: "Human",
          message: inputMessage
        }
        setMessages(messages => [...messages, newMessage])
        getResponse(inputMessage)
        messageBox.value = ""
      }
    } 

    const getResponse = async(input: string) => {
      const newResponse: messageItem = {
        sender: "AI",
        message: "Test response"
      }
      setMessages(messages => [...messages, newResponse])
    } 

    return (
      <div className={styles.chatBox}>
        <div>
          <ul>
            {messageList}
          </ul>
        </div>
        <div>
          <input type='text' id='inputMessage'/>
          <button onClick={handleSendMessage}>
            <Image
              src="/sendMessageIcon.svg"
              alt="send message"
              className={styles.sendMessageIcon}
              width={20}
              height={20}
              priority
            />
          </button>
        </div>
      </div>
    )
  }
  
  export default ChatBox
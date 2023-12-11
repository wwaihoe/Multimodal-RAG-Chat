"use client"

import styles from '../page.module.css' 
import Image from 'next/image'
import React, { useState, useEffect, useRef } from 'react'
import { v4 as uuidv4 } from 'uuid';

import ChatMessage from './ChatMessage'

interface messageItem {
    sender: string,
    message: string
  }

interface dialog {
  dialog: messageItem[]
}

const chatModelURL = "localhost"
const chatModelPort = "8080"


function ChatBox() {
    const [messages, setMessages] = useState<messageItem[] | []>([])
    const messagesEndRef = useRef<null | HTMLDivElement>(null)
    const messageList = messages.map((messageToDisplay) =>
        <ChatMessage key = {uuidv4()} sender = {messageToDisplay.sender} message = {messageToDisplay.message}/>
    )
    useEffect(() => {
      scrollToBottom()
    }, [messages]);

    const handleSendMessage = () => {
      const messageBox = document.getElementById("inputMessage") as HTMLInputElement
      if (messageBox) {
        messageBox.disabled = true
        const sendMessageButton = document.getElementById("sendMessageButton") as HTMLButtonElement
        sendMessageButton.disabled = true
        const inputMessage = messageBox.value
        const newMessage: messageItem = {
          sender: "Human",
          message: inputMessage
        }
        const currDialog: dialog = {
          dialog: [...messages, newMessage]
        }
        setMessages(messages => [...messages, newMessage])
        getResponse(currDialog)
        messageBox.value = ""
        messageBox.disabled = false
        sendMessageButton.disabled = false
      }
    } 

    const getResponse = async(dialog: dialog) => {
      try{
        const requestBody = JSON.stringify(dialog)
        const response = await fetch(`http://${chatModelURL}:${chatModelPort}/chat`, {
          method: 'POST', 
          body: requestBody
        })
        if (response.ok) {
          const responseBody = await response.text() 
          console.log(responseBody)
          const newResponse: messageItem = {
            sender: "AI",
            message: responseBody
          }
          setMessages(messages => [...messages, newResponse])
        }      
      }
      catch(err) {
        console.log(err)
      }
    } 

    const handleKeyMessage = (event: any) => {
      if (event.keyCode === 13) { 
        handleSendMessage()
      }
    }

    const scrollToBottom = () => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    return (
      <div className={styles.chatBox}>
        <div className={styles.messageList}>
          <ul>
            {messageList}
          </ul>
          <div ref={messagesEndRef} />
        </div>
        <div className={styles.chatInput}>
          <input type='text' id='inputMessage' onKeyDown={handleKeyMessage}/>
          <button id="sendMessageButton" onClick={handleSendMessage}>
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
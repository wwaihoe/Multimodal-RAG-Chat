"use client"

import styles from '../page.module.css' 
import Image from 'next/image'
import React, { useState } from 'react'
import { v4 as uuidv4 } from 'uuid';

//import ChatMessage from './ChatMessage'

interface messageItem {
    sender: string,
    message: string,
  }

function ChatBox() {
    const [currSender, setCurrSender] = useState(null)
    const [messages, setMessages] = useState<messageItem[] | []>([])
    const messageList = messages.map((message) =>
        <p>message</p>
        //<ChatMessage key = {uuidv4()} sender = {currSender} message = {message}/>
    )
    return (
      <div className={styles.chatBox}>
        <ul>
          {messageList}
        </ul>
        <input type='text' id='inputMessage'/>
        <button>
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
    )
  }
  
  export default ChatBox
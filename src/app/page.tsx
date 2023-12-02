import Image from 'next/image'
import styles from './page.module.css'

import FileLoader from './components/FileLoader'
import ChatBox from './components/ChatBox'

export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.description}>
        <h1>
          RAG chatbot
        </h1>
        <div>
          <Image
            src="/chatbotLogo.svg"
            alt="Chatbot Logo"
            className={styles.chatbotLogo}
            width={200}
            height={100}
            priority
          />
        </div>
      </div>
      <div className={styles.center}>
        <FileLoader/>
        <ChatBox/>
      </div>
    </main>
  )
}

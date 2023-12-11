import Image from 'next/image'
import styles from './page.module.css'

import FileLoader from './components/FileLoader'
import ChatBox from './components/ChatBox'


export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.sideBar}>
        <div className={styles.description}>
          <div>
            <Image
              src="/chatbotLogo.svg"
              alt="Chatbot Logo"
              className={styles.chatbotLogo}
              width={100}
              height={100}
              priority
            />
          </div>
          <h1>
            RAG Chat
          </h1>
        </div>
        <FileLoader/>
      </div>
      <div className={styles.center}>
        <ChatBox/>
      </div>
    </main>
  )
}

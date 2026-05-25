import { useState,useEffect, useRef } from "react";
import { sendMessage, resumeChat, fetchMessages } from "../api";
import { statusEnum, roleEnum } from "../enums/llm_response";
import SmartToyIcon from '@mui/icons-material/SmartToy';
import FaceIcon from '@mui/icons-material/Face';
import SendIcon from '@mui/icons-material/ArrowUpward';
import TableChartIcon from '@mui/icons-material/TableChart';

const quickChatTemplates = [
  {
    title: "Teacher roster",
    label: "Create teacher table",
    prompt:
      "Create a table named teacher for storing teacher records. The table should include an id column with integer type as the primary identifier, a name column with string/text type for the teacher's full name, and sensible constraints so id cannot be null and each teacher has a unique id. After creating the table, show me the final schema.",
  },
  {
    title: "Student directory",
    label: "Create student table",
    prompt:
      "Create a table named student for maintaining student information. Include an id column with integer type as the primary identifier, a name column with string/text type for the student's full name, an email column with string/text type that should be unique, and a grade column with integer type. Add appropriate not-null constraints for important fields and show me the resulting table schema.",
  },
  {
    title: "Course catalog",
    label: "Create course table",
    prompt:
      "Create a table named course for storing course catalog data. Include an id column with integer type as the primary identifier, a title column with string/text type for the course name, a code column with string/text type that should be unique, and credits as an integer column. Add constraints for required values, then return the created schema in a clear format.",
  },
];

export default function ChatBox({ threadId, setThreadId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [waitingForResume, setWaitingForResume] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

const chatBodyRef = useRef(null);
const isScrollRef = useRef(false);

  const handleSend = async () => {

    if (!input.trim()) return;

    const userMessage = {
      role: roleEnum.USER,
      content: input,
      timestamp: new Date(),
      status: statusEnum.COMPLETED,
    };



    setMessages((prev) => [...prev, userMessage]);
    

    setInput("");
    try {
      setIsSending(true);
      let response;

      if (waitingForResume) {
        response = await resumeChat(threadId, input);
      } else {
        response = await sendMessage(input, threadId);
      }

      // console.log("API Response:", response);

      if (!threadId && response.thread_id) {
        setThreadId(response.thread_id);
        localStorage.setItem("threadId", response.thread_id);
      }

      setMessages((prev) => [
          ...prev,
          {
            role: roleEnum.AGENT,
            content: response.response,
            status: response.status,
            timestamp: response.timestamp || new Date(),
          },
        ]);
        setWaitingForResume(response.status === statusEnum.INTERRUPT);
    } catch (err) {
      console.error("Failed to send message:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: roleEnum.AGENT,
          content: "Server error.",
          status: statusEnum.COMPLETED,
          timestamp: new Date(),
        },
      ]);
    }
    finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = async (event) => {
    if (event.key === 'Enter') {
      await handleSend();
    }
  };

  const handleTemplateClick = (template) => {
    setInput(template.prompt);
  };

  const scrollToBottom = () => {
    const container = chatBodyRef.current;

    if (!container) return;

    container.scrollTop = container.scrollHeight;
  };

  useEffect(() => {
    async function fetchInitialMessages() {
      if(threadId) {
        let res = await fetchMessages(threadId);
        setMessages(() => [...res]);
      }
    }
    fetchInitialMessages();
  }, [threadId]);

  useEffect(() =>{
    if(isScrollRef.current) {
      return;
    }
    setTimeout(() => {
          scrollToBottom();
        }, 0);
  }, [messages]);

  const loadMoreMessages = async () => {
    if (!threadId || loadingMore || !hasMore) return;

    const container = chatBodyRef.current;
    const oldScrollHeight = container.scrollHeight;

    setLoadingMore(true);

    try {
      const res = await fetchMessages(threadId, page + 1, 15);

      if (!res || res.length === 0) {
        setHasMore(false);
        return;
      }

      setMessages((prev) => [...res, ...prev]);
      setPage((prev) => prev + 1);

      setTimeout(() => {
        const newScrollHeight = container.scrollHeight;
        container.scrollTop = newScrollHeight - oldScrollHeight;
      }, 0);
    } finally {
      setLoadingMore(false);
    }
  };

  const handleScroll = () => {
    const container = chatBodyRef.current;

    if (!container) return;

    if (container.scrollTop === 0) {
      isScrollRef.current = true;
      loadMoreMessages();
      setTimeout(() => {
        isScrollRef.current = false;
      }, 100);
    }
  };

  return (

    <div className="container-fluid h-100 py-0 px-0">

      <div className="row d-flex justify-content-center h-100">
        <div className="col-md-12 col-lg-12 col-xl-12 ">

          <div className="card h-100" id="chat2">
            <div
              ref={chatBodyRef}
              onScroll={handleScroll}
              className="card-body"
              style={{
                position: "relative",
                height: "60vh",
                overflowY: "auto",
              }}
            >
              {loadingMore && (
                <div className="text-center text-muted small mb-2">
                  Loading older messages...
                </div>
              )}

              {!threadId && messages.length === 0 && (
                <section className="quick-chat-panel" aria-label="Quick chat templates">
                  <div className="quick-chat-panel__header">
                    <span>Start with a template</span>
                    <h4>Build your first dataset faster</h4>
                  </div>

                  <div className="quick-chat-grid">
                    {quickChatTemplates.map((template) => (
                      <button
                        key={template.title}
                        className="quick-chat-card"
                        type="button"
                        onClick={() => handleTemplateClick(template)}
                      >
                        <TableChartIcon fontSize="small" />
                        <span>{template.title}</span>
                        <strong>{template.label}</strong>
                        <p>{template.prompt}</p>
                      </button>
                    ))}
                  </div>
                </section>
              )}

              <div>
                {messages.map((msg, index) => (
                  <div
                    key={msg.id || index}
                    className={`d-flex flex-row justify-content-${
                      msg.role === roleEnum.USER ? "end" : "start"
                    }`}
                  >
                    {msg.role === roleEnum.AGENT && (
                      <SmartToyIcon style={{ width: "40px", height: "40px" }} />
                    )}

                    <div>
                      <p
                        className={`small p-2 ${
                          msg.role === roleEnum.USER
                            ? "text-white bg-primary"
                            : "bg-body-tertiary"
                        } rounded-3 ms-3 mb-1 text-start`}
                      >
                        {msg.content}
                      </p>

                      <p
                        className={`small ms-3 mb-3 rounded-3 text-muted d-flex justify-content-${
                          msg.role === roleEnum.USER ? "end" : "start"
                        }`}
                      >
                        {msg.timestamp
                          ? new Date(
                              typeof msg.timestamp === "string"
                                ? msg.timestamp.replace(" ", "T")
                                : msg.timestamp
                            ).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : ""}
                      </p>
                    </div>

                    {msg.role === roleEnum.USER && (
                      <FaceIcon
                        className="ms-3"
                        style={{ width: "40px", height: "40px" }}
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
            <div className="card-footer text-muted d-flex justify-content-start align-items-center p-3">
              <FaceIcon className="me-3" style={{width: "40px", height: "100%"}}/>
              <input type="text" className="form-control form-control-lg" id="exampleFormControlInput1"
                placeholder="Type message" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown}/>
              <button className="send-button ms-2" id="button-addon2" onClick={handleSend} disabled={isSending}><SendIcon style={{width: "20px", height: "20px", color:"black"}}/></button>
            </div>
          </div>

        </div>
      </div>

  </div>
  );
}

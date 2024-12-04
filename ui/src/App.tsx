import { FormEvent, useState } from 'react';
import './App.css';
import { Button, Col, Container, Form, FormControl, Row } from 'react-bootstrap';
import { MessageService } from './service/MessageService';

interface Message {
  message: string;
  isBot: boolean;
}

export function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const messageService = new MessageService();

  const handleSendMessage = async (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() !== '') {
      // Add the user's message first
      const newMessages = [{ message: input, isBot: false }, ...messages];
      setMessages(newMessages);

      // Get bot's response and add it to the messages array
      const { querySQL, interpretedResult } = await messageService.getResponse(input);
      setMessages([{ message: interpretedResult, isBot: true }, { message: querySQL, isBot: true }, ...newMessages]);

      setInput('');
    }
  };

  return (
    <>
      <h3>Runner Database Chatbot</h3>
      <Container style={{ height: '80vh', width: '70vw', display: 'flex', flexDirection: 'column' }}>
        <Row className="flex-grow-1" style={{ overflowY: 'auto', padding: '10px', border: '1px solid lightgray' }}>
          <Col style={{ display: 'flex', flexDirection: 'column-reverse' }}>
            {messages.map((message, index) => (
              <div key={index} className="mb-3" style={{ display: 'flex', maxWidth: '80%', alignSelf: message.isBot ? 'flex-start' : 'flex-end' }}>
                <div
                  className="p-2 bg-light rounded"
                  style={{
                    border: `2px solid ${message.isBot ? 'blue' : 'green'}`,
                  }}>
                  {message.message}
                </div>
              </div>
            ))}
          </Col>
        </Row>

        <Row style={{ padding: '10px' }}>
          <Col>
            <Form onSubmit={handleSendMessage} className="d-flex">
              <FormControl type="text" placeholder="Type your query..." value={input} onChange={(e) => setInput(e.target.value)} />
              <Button variant="primary" type="submit" className="ml-2">
                Send
              </Button>
            </Form>
          </Col>
        </Row>
      </Container>
    </>
  );
}

export class MessageService {
  async getResponse(message: string): Promise<{ querySQL: string; interpretedResult: string }> {
    const response = await fetch('http://localhost:3000/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: message }),
    });
    const res = await response.json();
    return res;
  }
}

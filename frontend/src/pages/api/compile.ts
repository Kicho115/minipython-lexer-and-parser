import type { NextApiRequest, NextApiResponse } from 'next';

type ResponseData = {
  output: string;
  error?: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ output: '', error: 'Method not allowed' });
  }

  try {
    const { code } = req.body;

    if (!code) {
      return res.status(400).json({ output: '', error: 'No code provided' });
    }

    // TODO: Implement the actual compilation logic here
    // This is where you'll integrate with your lexer and parser
    // For now, we'll just echo the code back
    return res.status(200).json({ output: `Received code:\n${code}` });
  } catch (error) {
    console.error('Compilation error:', error);
    return res.status(500).json({ 
      output: '', 
      error: 'An error occurred during compilation' 
    });
  }
} 
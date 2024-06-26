import express from 'express';
import { fetchUserDetails } from './api/fetchUserDetails.js';

const app = express();
const port = 3000;

app.get('/user/:username', (req, res) => {
    const username = req.params.username;
    fetchUserDetails(username, res);
});

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});

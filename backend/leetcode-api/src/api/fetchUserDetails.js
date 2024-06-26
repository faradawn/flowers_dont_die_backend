import fetch from 'node-fetch';
import userProfileQuery from '../graphql/queries.js';

export const fetchUserDetails = async (username, res) => {
    try {
        const response = await fetch('https://leetcode.com/graphql', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Referer': 'https://leetcode.com',
            },
            body: JSON.stringify({
                query: userProfileQuery,
                variables: {
                    username: username,
                },
            }),
        });

        const result = await response.json();

        if (result.errors) {
            return res.status(400).json(result);
        }

        return res.json(result.data);
    } catch (err) {
        console.error('Error fetching user details:', err);
        return res.status(500).json({ error: 'Internal server error' });
    }
};

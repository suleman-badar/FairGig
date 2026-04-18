const request = require('supertest');
const app = require('../src/index');

describe('Grievance health', () => {
    it('returns health', async () => {
        const response = await request(app).get('/health');
        expect(response.statusCode).toBe(200);
        expect(response.body.service).toBe('grievance');
    });
});

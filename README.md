# Daily Chinese Vocab

A serverless app that sends a Chinese word as a daily email message, along with links to example sentences and auto-generated quizzes.

Chinese learners can subscribe to daily vocab words to build their vocabulary. The vocabulary by level (1-6) is from the Hanyu Shuiping Kaoshi (HSK), China's standardized Mandarin testing levels.

To subscribe, visit https://haohaotiantian.com, where you can preview sample words for each level, see past daily words, and learn more.

## Example message

![Example message](https://hhtt-static.s3.amazonaws.com/email-screenshot-wide.png)

## Architecture

You can learn about the development process and architecture decisions in this talk:
- [Getting started building your first serverless web application](https://www.youtube.com/watch?v=DdyhdnWVukc)

And in this blog post series:
- [Developing a daily Chinese vocab app](https://emshea.com/post/chinese-vocab-app)
- [Integrating DynamoDB in my Chinese vocab app](https://emshea.com/post/vocab-app-database)
- [Migrating to a serverless contact management backend](https://emshea.com/post/vocab-subscriber-backend)

[Front end repo](https://github.com/em-shea/vocab-frontend-vue)

![Architectural diagram](https://hsk-vocab.s3.amazonaws.com/vocab-app-v7-profiles1.png)

## Roadmap

| Roadmap item | Status |
| ------------- | :-------------: |
| Store user quiz results | |
| User practice sentences | |
| User created vocab lists | |
| 成语 vocab list | |
| Add pronunciation audio | |
| Add user profiles | :heavy_check_mark: |
| Auto-generated quizzes | :heavy_check_mark: |
| Build subscriber analytics QuickSight dashboard | :heavy_check_mark: |
| Add support for traditional characters | :heavy_check_mark: |
| Build interface for users to explore and export word history | :heavy_check_mark: |
| Create API to serve daily word history | :heavy_check_mark: |
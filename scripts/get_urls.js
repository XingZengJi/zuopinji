import axios from 'axios';

const APP_ID = 'cli_a95e5f9bf2785cce';
const APP_SECRET = 'oiHkkTg9r8CgqrcrMZG9bbhmZVZGjZkh';

async function getAccessToken() {
  const resp = await axios.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
    app_id: APP_ID,
    app_secret: APP_SECRET
  });
  return resp.data.tenant_access_token;
}

async function getTmpUrls(tokens, token) {
  const resp = await axios.post(
    'https://open.feishu.cn/open-apis/drive/v1/medias/batch_get_tmp_download_url',
    { file_tokens: tokens },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return resp.data.data?.results || [];
}

async function main() {
  const accessToken = await getAccessToken();

  const coverTokens = [
    'TeNwbothNoPl0xxvsIocCcRqnoe',  // 视频封面
    'AAQ9bUMxQogyx2x0t48chPqtnKb'  // 图片封面
  ];

  const fileTokens = [
    'ZbWIbQJ8FonY2kxVPVXcFbqrnZc',  // 视频
    'BoFjbHYGLocw3wxFqHPc4HRAnMg'   // 图片
  ];

  const allTokens = [...coverTokens, ...fileTokens];
  const results = await getTmpUrls(allTokens, accessToken);

  console.log(JSON.stringify(results, null, 2));
}

main().catch(console.error);

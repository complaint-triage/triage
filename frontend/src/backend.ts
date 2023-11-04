import { JSONRPCClient } from 'json-rpc-2.0'

const rpcAddress = ''
const rpcEndpoint = '/t/rpc'

export class Backend {
    protected _base: string;
    protected _rpcClient: JSONRPCClient<void>;

    constructor() {
        this._base = rpcAddress + rpcEndpoint;
        this._rpcClient = new JSONRPCClient<void>(
            async (request) => {
                console.log('RPC ->', request)
                const response = await fetch(this._base, {
                    method: 'POST',
                    headers: {
                        'content-type': 'application/json'
                    },
                    body: JSON.stringify(request)
                })
                if (response.status === 200) {
                    const responseJSON = await response.json()
                    console.log('RPC <-', responseJSON)
                    this._rpcClient.receive(responseJSON)
                } else {
                    throw new Error('Unexpected rpc response' + response.statusText)
                }
            }
        )
    }

    get rpcClient() {
        return this._rpcClient
    }
}
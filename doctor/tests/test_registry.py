import registry
import pytest

"""
# NOTE: ADD A DELEGATE (costs gas)
@pytest.mark.asyncio
async def test_add_delegate():
    txn = await registry.add_delegate(
        '0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2',
        'DID-JWT',
        '0x72D2498093BDD45f26049178a331BE851b4f90c4',
        31536000
    )
    print(txn)
"""

@pytest.mark.asyncio
async def test_valid_delegate():
    txn = await registry.valid_delegate(
        '0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2',
        'DID-JWT',
        '0x2e3D6752536566ED51c805A86070BA596052FCb6',
    )
    assert txn == False

    txn = await registry.valid_delegate(
        '0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2',
        'DID-JWT',
        '0x72D2498093BDD45f26049178a331BE851b4f90c4',
    )

    assert txn == True

    txn = await registry.valid_delegate(
        '0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2',
        'DID-JWT',
        '0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2',
    )

    assert txn == False

    txn = await registry.is_doctor('0x72D2498093BDD45f26049178a331BE851b4f90c4')
    assert txn == True

    txn = await registry.is_doctor('0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2')
    assert txn == True




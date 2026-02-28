'use client';

import { useState, useEffect } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Loader2 } from 'lucide-react';
import type { Client, ClientCreate, EntityType } from '@/lib/api/types';

const entityTypes: { value: EntityType; label: string }[] = [
    { value: 'partnership', label: 'Partnership' },
    { value: 'proprietorship', label: 'Proprietorship' },
    { value: 'company', label: 'Company' },
    { value: 'llp', label: 'LLP' },
    { value: 'trading', label: 'Trading' },
];

interface ClientFormModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    client: Client | null;
    onSave: (data: ClientCreate) => Promise<void>;
    isLoading?: boolean;
}

export function ClientFormModal({
    open,
    onOpenChange,
    client,
    onSave,
    isLoading = false,
}: ClientFormModalProps) {
    const [formData, setFormData] = useState<ClientCreate>({
        name: '',
        entity_type: 'company',
        pan: '',
        gst: '',
        contact_person: '',
        email: '',
        phone: '',
        address: '',
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    useEffect(() => {
        if (client) {
            setFormData({
                name: client.name,
                entity_type: client.entity_type,
                pan: client.pan || '',
                gst: client.gst || '',
                contact_person: client.contact_person || '',
                email: client.email || '',
                phone: client.phone || '',
                address: client.address || '',
            });
        } else {
            setFormData({
                name: '',
                entity_type: 'company',
                pan: '',
                gst: '',
                contact_person: '',
                email: '',
                phone: '',
                address: '',
            });
        }
        setErrors({});
    }, [client, open]);

    const validate = (): boolean => {
        const newErrors: Record<string, string> = {};
        if (!formData.name.trim()) newErrors.name = 'Name is required';
        if (!formData.entity_type) newErrors.entity_type = 'Entity type is required';
        if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
            newErrors.email = 'Invalid email format';
        }
        if (formData.pan && !/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(formData.pan.toUpperCase())) {
            newErrors.pan = 'Invalid PAN format';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!validate()) return;
        await onSave(formData);
    };

    const updateField = (key: keyof ClientCreate, value: string) => {
        setFormData((prev) => ({ ...prev, [key]: value }));
        if (errors[key]) {
            setErrors((prev) => {
                const next = { ...prev };
                delete next[key];
                return next;
            });
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-lg" style={{ backgroundColor: 'var(--bg-card)' }}>
                <DialogHeader>
                    <DialogTitle>{client ? 'Edit Client' : 'Add New Client'}</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Name */}
                    <div className="space-y-1.5">
                        <label className="text-sm font-medium text-foreground">
                            Client Name <span className="text-destructive">*</span>
                        </label>
                        <Input
                            value={formData.name}
                            onChange={(e) => updateField('name', e.target.value)}
                            placeholder="e.g., Mehta Computers Pvt Ltd"
                            className="bg-background/50 border-border/30"
                        />
                        {errors.name && <p className="text-xs text-destructive">{errors.name}</p>}
                    </div>

                    {/* Entity Type */}
                    <div className="space-y-1.5">
                        <label className="text-sm font-medium text-foreground">
                            Entity Type <span className="text-destructive">*</span>
                        </label>
                        <Select
                            value={formData.entity_type}
                            onValueChange={(val) => updateField('entity_type', val)}
                        >
                            <SelectTrigger className="bg-background/50 border-border/30">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent style={{ backgroundColor: 'var(--bg-card)' }}>
                                {entityTypes.map((type) => (
                                    <SelectItem key={type.value} value={type.value}>
                                        {type.label}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        {errors.entity_type && <p className="text-xs text-destructive">{errors.entity_type}</p>}
                    </div>

                    {/* PAN & GST */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-foreground">PAN</label>
                            <Input
                                value={formData.pan}
                                onChange={(e) => updateField('pan', e.target.value.toUpperCase())}
                                placeholder="ABCDE1234F"
                                maxLength={10}
                                className="bg-background/50 border-border/30"
                            />
                            {errors.pan && <p className="text-xs text-destructive">{errors.pan}</p>}
                        </div>
                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-foreground">GST</label>
                            <Input
                                value={formData.gst}
                                onChange={(e) => updateField('gst', e.target.value.toUpperCase())}
                                placeholder="22ABCDE1234F1Z5"
                                maxLength={15}
                                className="bg-background/50 border-border/30"
                            />
                        </div>
                    </div>

                    {/* Contact Person & Email */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-foreground">Contact Person</label>
                            <Input
                                value={formData.contact_person}
                                onChange={(e) => updateField('contact_person', e.target.value)}
                                placeholder="Full name"
                                className="bg-background/50 border-border/30"
                            />
                        </div>
                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-foreground">Email</label>
                            <Input
                                type="email"
                                value={formData.email}
                                onChange={(e) => updateField('email', e.target.value)}
                                placeholder="client@example.com"
                                className="bg-background/50 border-border/30"
                            />
                            {errors.email && <p className="text-xs text-destructive">{errors.email}</p>}
                        </div>
                    </div>

                    {/* Phone & Address */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-foreground">Phone</label>
                            <Input
                                value={formData.phone}
                                onChange={(e) => updateField('phone', e.target.value)}
                                placeholder="+91 9876543210"
                                className="bg-background/50 border-border/30"
                            />
                        </div>
                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-foreground">Address</label>
                            <Input
                                value={formData.address}
                                onChange={(e) => updateField('address', e.target.value)}
                                placeholder="City, State"
                                className="bg-background/50 border-border/30"
                            />
                        </div>
                    </div>

                    <DialogFooter className="pt-2">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => onOpenChange(false)}
                            className="border-border/30"
                        >
                            Cancel
                        </Button>
                        <Button
                            type="submit"
                            className="bg-gold hover:bg-gold-hover text-primary-foreground font-semibold"
                            disabled={isLoading}
                        >
                            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            {client ? 'Update' : 'Create'}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
